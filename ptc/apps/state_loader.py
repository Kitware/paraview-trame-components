import paraview.web.venv  # noqa: F401
from paraview import simple

import ptc
from pathlib import Path
from trame.app import get_server


class StateLoader(ptc.Viewer):
    def __init__(self, state_path=None, data_directory=None):
        server = get_server()
        if state_path is None and data_directory is None:
            server.cli.add_argument(
                "--state", help="Path to state file to load", required=True
            )
            server.cli.add_argument("--data-directory", help="Path to data directory")
            args, _ = server.cli.parse_known_args()

            state_path = str(Path(args.state).resolve())
            data_directory = args.data_directory

        if data_directory is None:
            data_directory = str(Path(state_path).parent.resolve())

        simple.LoadState(
            state_path,
            data_directory=data_directory,
            restrict_to_data_directory=True,
        )

        super().__init__(from_state=True)


def main():
    app = StateLoader()
    app.start()


if __name__ == "__main__":
    main()
