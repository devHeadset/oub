{
  pkgs ? import <nixpkgs> {}
}:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.python311Packages.aiohttp
    pkgs.python311Packages.python-dotenv
  ];

  shellHook = ''
    echo "setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install interactions.py
    echo "environment ready."
  '';
}
