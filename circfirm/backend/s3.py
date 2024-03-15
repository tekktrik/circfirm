# SPDX-FileCopyrightText: 2024 Alec Delaney, for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Backend functionality for the working with the CircuitPython firmware S3 bucket.

Author(s): Alec Delaney
"""

import re
from typing import List, Optional

import boto3
import botocore
import botocore.client
import packaging.version
from mypy_boto3_s3 import S3ServiceResource

import circfirm.backend
import circfirm.backend.cache

S3_CONFIG = botocore.client.Config(signature_version=botocore.UNSIGNED)
S3_RESOURCE: S3ServiceResource = boto3.resource("s3", config=S3_CONFIG)
BUCKET_NAME = "adafruit-circuit-python"
BUCKET = S3_RESOURCE.Bucket(BUCKET_NAME)


def get_board_versions(
    board_id: str, language: str = "en_US", *, regex: Optional[str] = None
) -> List[str]:
    """Get a list of CircuitPython versions for a given board."""
    prefix = f"bin/{board_id}/{language}"
    firmware_regex = circfirm.backend.FIRMWARE_REGEX_PATTERN.replace(
        r"[board]", board_id
    ).replace(r"[language]", language)
    version_regex = circfirm.backend._VALID_VERSIONS_CAPTURE
    firmware_regex = firmware_regex.replace(r"[version]", version_regex)
    s3_objects = BUCKET.objects.filter(Prefix=prefix)
    versions = set()
    for s3_object in s3_objects:
        result = re.match(f"{prefix}/{firmware_regex}", s3_object.key)
        if result:
            if regex:
                firmware_filename = s3_object.key.split("/")[-1]
                version, _ = circfirm.backend.parse_firmware_info(firmware_filename)
                if not re.match(regex, version):
                    continue
            versions.add(result[1])
    return sorted(versions, key=packaging.version.Version, reverse=True)


def get_latest_board_version(
    board_id: str, language: str, pre_release: bool
) -> Optional[str]:
    """Get the latest version for a board in a given language."""
    versions = get_board_versions(board_id, language)
    if not pre_release:
        versions = [
            version
            for version in versions
            if not packaging.version.Version(version).is_prerelease
        ]
    if versions:
        return versions[0]
    return None
