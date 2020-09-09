import os

# The full version, including alpha/beta/rc tags.
release = os.popen('git describe --tags --dirty').read().strip()
print(release)

release_parts = release.split('-')
basic_version = release_parts[0]
commits_since_tag = release_parts[1] if len(release_parts) > 1 else None
sha = release_parts[2] if len(release_parts) > 2 else None
dirty_flag = release_parts[3] if len(release_parts) > 3 else None

with open(os.path.join("EDScoutWebUI", "version.py"), "w") as f:
    f.write(f'release = "{release}"\n')
    f.write(f'version = "{basic_version}"\n')

with open(os.path.join("Installer", "version.txt"), "w") as f:
    f.write(f'{release}')