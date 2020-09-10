import os
import re
from jinja2 import Environment, FileSystemLoader

def extract_version_parts(git_response):
    regex = r"v(\d)\.(\d)\.(\d)(?:-(\d+)-([a-z0-9]+)(?:-([a-z0-9]+))?)?"

    matches = re.finditer(regex, git_response, re.MULTILINE)

    groups = list(matches)[0].groups()
    if len(groups) > 3:
        commits_since_tag = groups[3]
        commit_sha = groups[4]
    else:
        commits_since_tag = 0
        commit_sha = None
    four_part_version = list(groups[0:3]) + [commits_since_tag]

    version_info = {
        'four_part_version': four_part_version,
        'is_dirty': (len(groups) > 4)
    }
    return version_info


# The full version, including alpha/beta/rc tags.
release = os.popen('git describe --tags --dirty').read().strip()
print(release)  # Returns something like v1.5.1-4-gc25ef16-dirty

release_parts = release.split('-')
basic_version = release_parts[0]
commits_since_tag = release_parts[1] if len(release_parts) > 1 else None
sha = release_parts[2] if len(release_parts) > 2 else None
dirty_flag = release_parts[3] if len(release_parts) > 3 else None

# Write the version used to display version info in the web gui and logs.
with open(os.path.join("../EDScoutWebUI", "version.py"), "w") as f:
    f.write(f'release = "{release}"\n')
    f.write(f'version = "{basic_version}"\n')

# record the version more simply here to aid the packaging process
with open("version.txt", "w") as f:
    f.write(f'{release}')

env = Environment(
    loader=FileSystemLoader('.'),
)

template = env.get_template('version_template.txt')

version_parts = extract_version_parts(release)
csv_version = ', '.join(version_parts['four_part_version'])  # Something like 1,5,1,0
short_version = '.'.join(version_parts['four_part_version'][0:3])  # Something like 1.5.1
long_version = release  # Something like v1.5.1-4-gc25ef16-dirty

rendered_verion_file = template.render(csv_version=csv_version, short_version=short_version, long_version=long_version)
# print(rendered_verion_file)

with open("version_for_installer.txt", "w") as f:
    f.write(rendered_verion_file)
