import os
import re
from pathlib import Path
from src.utils import logger


def update_build():
    try:
        version_path = Path(os.getcwd()).parent / 'version.txt'
        if os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用正则找到Build
            match = re.search(r"StringStruct\(u'Build',\s*u'(\d+)'\)", content)
            if match:
                current_build_number = int(match.group(1))
                new_build_number = current_build_number + 1
                # 使用新的Build替换
                new_content = re.sub(
                    r"(StringStruct\(u'Build',\s*u')(\d+)(')",
                    r"\g<1>" + str(new_build_number) + r"\g<3>",
                    content
                )
                with open(version_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"Updated build number in version.txt from {current_build_number} to {new_build_number}")
            else:
                logger.warning("Could not find 'Build' number in version.txt")
    except Exception as e:
        logger.error(f"Failed to update build number: {e}")
