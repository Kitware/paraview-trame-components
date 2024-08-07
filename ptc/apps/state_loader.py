import paraview.web.venv  # noqa: F401
from paraview import simple

import ptc
from pathlib import Path
from trame.app import get_server

server = get_server()
server.cli.add_argument("--state", help="Path to state file to load", required=True)
server.cli.add_argument("--data-directory", help="Path to data directory")

args, _ = server.cli.parse_known_args()

state_file = str(Path(args.state).resolve())
data_dir = args.data_directory

if data_dir is None:
    data_dir = str(Path(state_file).parent.resolve())

simple.LoadState(
    state_file,
    data_directory=data_dir,
    restrict_to_data_directory=True,
)

web_app = ptc.Viewer(from_state=True)
web_app.start()
