"""Add required flags to output gcloud run deploy command."""

from typing import List
import pkg_resources

def translate_add_required_flags() -> List[str]:
    """Add required flags to gcloud run deploy command."""
    labels: str = _get_labels()
    return [
        '--no-cpu-throttling',
        '--allow-unauthenticated',
        f'--labels={labels}'
    ]

def _get_labels() -> str:
    labels: List[str] = []
    labels.append('migrated-from=app-engine')
    version = pkg_resources.require('app2run')[0].version.replace('.', '_')
    labels.append(f'app2run-version={version}')
    return ",".join(labels)
