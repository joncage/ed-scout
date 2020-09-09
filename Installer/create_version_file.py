import os
from jinja2 import Template

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

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('.'),
)

template = env.get_template('version_template.txt')

version_parts = basic_version.split()
csv_version = ''  # Something like 1,5,1,0
short_version = basic_version  # Something like 1.5.1
long_version = release  # Something like v1.5.1-4-gc25ef16-dirty

print(template.render(csv_version='1,2,3,4', short_version=short_version, long_version=long_version))

exit(0)
