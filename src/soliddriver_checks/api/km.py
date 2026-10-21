import os
import shlex
import pandas as pd
import json
from ..config import SDCConf
from enum import Enum, unique
from .utils.cmd import run_cmd


@unique
class KMEvaluation(Enum):
    PASS = 1
    WARNING = 2
    ERROR = 3

    def __str__(self):
        return self.name

    def __int__(self):
        return self.value

    def to_json(self):
        return {"level": self.name, "value": self.value}


KM_COLUMNS = [
    "level",
    "modulename",
    "filename",
    "license",
    "signature",
    "supported",
    "running",
    "kmp",
]


class KMAnalysis:
    def __init__(self):
        conf = SDCConf()
        self._valid_licenses = conf.get_valid_licenses()
        self._valid_licenses = [i.get("name", "") for i in self._valid_licenses]

    def kms_analysis(self, kms):
        df = pd.DataFrame(columns=KM_COLUMNS)
        for filename in kms:
            row_level = []
            lev_name, name = self._km_module_name_analysis(
                kms[filename].get("name", "")
            )
            row_level.append(lev_name["value"])
            lev_fn, filename = self._km_filename_analysis(
                filename, kms[filename].get("weak-updates", 0)
            )
            row_level.append(lev_fn["value"])
            lev_spd, supported = self._km_supported_analysis(
                kms[filename].get("supported", "")
            )
            row_level.append(lev_spd["value"])
            lev_lic, license = self._km_license_analysis(
                kms[filename].get("license", "")
            )
            row_level.append(lev_lic["value"])
            lev_sig, signature = self._km_signature_analysis(
                kms[filename].get("signature", "")
            )
            row_level.append(lev_sig["value"])
            lev_r, running = self._km_running_analysis(kms[filename].get("running", ""))
            row_level.append(lev_r["value"])
            lev_kmp, kmp = self._km_kmp_analysis(kms[filename].get("kmp", None))
            row_level.append(lev_kmp["value"])

            row = pd.Series(
                {
                    "level": KMEvaluation(max(row_level)).to_json(),
                    "modulename": {"level": lev_name, "value": name},
                    "filename": {"level": lev_fn, "value": filename},
                    "license": {"level": lev_lic, "value": license},
                    "signature": {"level": lev_sig, "value": signature},
                    "supported": {
                        "level": lev_spd,
                        "value": " ".join(supported).strip(),
                    },
                    "running": {"level": lev_r, "value": running},
                    "kmp": {"level": lev_kmp, "value": kmp},
                }
            )

            if len(df.index) == 0:
                df = row.to_frame().T
            else:
                df = pd.concat([df, row.to_frame().T], ignore_index=True)

        return df

    def _km_module_name_analysis(self, name):
        return KMEvaluation.PASS.to_json(), name

    def _km_filename_analysis(self, filename, wu):
        lev = KMEvaluation.PASS
        if not filename.startswith(("/lib/modules/", "/usr/lib/modules/")):
            lev = KMEvaluation.WARNING

        if wu != 0:  # under weak-updates folder, and have issues.
            if wu == 2 or wu == 3:  # kernel module does not exist or not a link
                lev = KMEvaluation.ERROR

        return lev.to_json(), filename

    def _km_supported_analysis(self, supported):
        sps = supported.splitlines()
        lev = KMEvaluation.PASS
        # no supported flag or 1 supported flag but the value is not yes(supported by SUSE) or supported (supported by others).
        if len(sps) == 0 or (
            len(sps) == 1
            and sps[0] != "yes"
            and sps[0] != "no"
            and sps[0] != "external"
        ):
            lev = KMEvaluation.ERROR
        elif len(sps) > 1:
            lev = KMEvaluation.WARNING
            for v in sps:
                if v != "yes" and v != "no" and v != "external":
                    lev = KMEvaluation.ERROR
                    break

        return lev.to_json(), sps

    def _km_license_analysis(self, license):
        lev = KMEvaluation.PASS

        lics = license.split("\n")
        for i in lics:
            if i not in self._valid_licenses:
                lev = KMEvaluation.WARNING
                break

        return lev.to_json(), license

    def _km_signature_analysis(self, signature):
        if signature != "":
            return KMEvaluation.PASS.to_json(), "Yes"
        else:
            return KMEvaluation.WARNING.to_json(), "No"

    def _km_running_analysis(self, running):
        return KMEvaluation.PASS.to_json(), running

    def _km_kmp_analysis(self, kmp):
        if kmp is None:
            return KMEvaluation.PASS.to_json(), ""

        name = kmp["name"]
        signature = kmp["signature"]

        if name.endswith("is not owned by any package"):
            return KMEvaluation.WARNING.to_json(), "Not owned by any package"
        elif signature == "":
            return KMEvaluation.WARNING.to_json(), name + ": has no signature"

        return KMEvaluation.PASS.to_json(), name


class KMReader:
    # resolve OSError: [Errno 7] Argument list too long: '/bin/sh'
    def _split_cmd_args(self, files, cmd):
        files_no = len(files)
        output = ""
        step = 300
        for i in range(0, files_no, step):
            str_files = " ".join(shlex.quote(f) for f in files[i : i + step])
            output += run_cmd(cmd % str_files)

        return output

    @staticmethod
    def _canonical(path):
        # resolve directory symlinks (e.g. /lib -> /usr/lib) like "rpm -qf" does,
        # but not the file itself, so weak-updates links stay unowned.
        return os.path.join(os.path.realpath(os.path.dirname(path)), os.path.basename(path))

    def _get_kms_owner(self):
        """Map every kernel module file in the rpm database to its package."""
        output = run_cmd(
            "rpm -qa --qf '[%{FILENAMES}\\t%{=NAME}-%{=VERSION}-%{=RELEASE}.%{=ARCH}\\n]'"
            " | grep -E '\\.(ko|ko\\.xz|ko\\.zst)\\s'"
        )
        owners = {}
        for line in output.splitlines():
            file, sep, pkg = line.partition("\t")
            if sep:
                owners[self._canonical(file)] = pkg

        return owners

    def _get_kmps_signature(self):
        """Map every installed package to its signature, "" if unsigned."""
        # same expression "rpm -q --info" uses for its "Signature" line
        sig = "%|DSAHEADER?{%{DSAHEADER:pgpsig}}:{%|RSAHEADER?{%{RSAHEADER:pgpsig}}:{(none)}|}|"
        output = run_cmd(
            "rpm -qa --qf '%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}\\t%s\\n'" % sig
        )
        signatures = {}
        for line in output.splitlines():
            pkg, sep, signature = line.partition("\t")
            if sep:
                signature = signature.strip()
                signatures[pkg] = "" if signature == "(none)" else signature

        return signatures

    def get_all_modinfo(self):
        running_kms = run_cmd(
            "/usr/sbin/modinfo $(cat /proc/modules | awk '{print $1}') | grep filename | awk '{print$2}'"
        ).splitlines()
        # Have to remove the invalid running kernel module, like it's running inside container.
        # But it always can't get rpm information if it's running inside container.
        running_kms = [
            file for file in running_kms if not file.startswith("modinfo: ERROR:")
        ]
        lm_kms = run_cmd(
            r'find /lib/modules/ -regex ".*\.\(ko\|ko.xz\|ko.zst\)$"'
        ).splitlines()

        files = sorted(set(running_kms + lm_kms))
        if len(files) == 0:
            return {}

        # we don't need the entire signature, so add grep to ignore the details in other lines.
        # modinfo prints nothing for a broken link, so key the output by its
        # "filename:" line instead of relying on the order of files.
        modinfo = self._split_cmd_args(
            files, '/usr/sbin/modinfo %s 2>/dev/null | grep -E "^([a-z]|[A-Z])"'
        )
        kms = {}
        info = None
        for line in modinfo.splitlines():
            k, sep, v = line.partition(":")
            if not sep:
                continue
            k, v = k.strip(), v.strip()
            if k == "filename":
                info = kms.setdefault(v, {})
            elif info is None:
                continue
            elif k in info:  # if already exist
                info[k] = info[k] + "\n" + v
            else:
                info[k] = v

        for file in files:  # broken modules or links still need to be reported
            kms.setdefault(file, {})

        owners = self._get_kms_owner()
        signatures = self._get_kmps_signature()
        for filename in kms:
            kms[filename]["running"] = filename in running_kms
            pkg = owners.get(self._canonical(filename))
            if pkg is None:  # weak-updates links belong to the package of their target
                pkg = owners.get(os.path.realpath(filename))
            if pkg is None:
                kms[filename]["kmp"] = {
                    "name": "file %s is not owned by any package" % filename,
                    "signature": "",
                }
            else:
                kms[filename]["kmp"] = {
                    "name": pkg,
                    "signature": signatures.get(pkg, ""),
                }

        self._check_weak_links(kms)

        return kms

    def _check_weak_links(self, kms):
        pkg_path = os.path.dirname(__file__)
        script = f"{pkg_path}/utils/scripts/check-links.sh"
        j_links = run_cmd("bash %s" % shlex.quote(script))
        links = json.loads(j_links)
        for km in links["weak-updates"]:
            filename = km.get("km", None)
            if filename in kms:
                kms[filename]["weak-updates"] = km.get("status", 0)
