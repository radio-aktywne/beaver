{
  inputs = {
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    };

    flake-parts = {
      url = "github:hercules-ci/flake-parts";
    };
  };

  outputs = inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      # Import local override if it exists
      imports = [
        (
          if builtins.pathExists ./local.nix
          then ./local.nix
          else {}
        )
      ];

      # Sensible defaults
      systems = [
        "x86_64-linux"
        "i686-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem = {
        config,
        lib,
        pkgs,
        system,
        ...
      }: let
        node = pkgs.nodejs;
        python = pkgs.python312;
        nil = pkgs.nil;
        task = pkgs.go-task;
        coreutils = pkgs.coreutils;
        trunk = pkgs.trunk-io;
        poetry = pkgs.poetry;
        cacert = pkgs.cacert;
        copier = pkgs.copier;
        openssl = pkgs.openssl;
        usql = pkgs.usql;
        tini = pkgs.tini;
        su-exec = pkgs.su-exec;
      in {
        # Override pkgs argument
        _module.args.pkgs = import inputs.nixpkgs {
          inherit system;
          config = {
            # Allow packages with non-free licenses
            allowUnfree = true;
            # Allow packages with broken dependencies
            allowBroken = true;
            # Allow packages with unsupported system
            allowUnsupportedSystem = true;
          };
        };

        # Set which formatter should be used
        formatter = pkgs.alejandra;

        # Define multiple development shells for different purposes
        devShells = {
          default = pkgs.mkShell {
            name = "dev";

            packages = [
              node
              python
              nil
              task
              coreutils
              trunk
              poetry
              cacert
              copier
              openssl
              usql
            ];

            EXTRAPYTHONPATH = "${python}/${python.sitePackages}";

            shellHook = ''
              export TMPDIR=/tmp
              export PRISMA_DB_URL="postgres://user:''${BEAVER__SAPPHIRE__SQL__PASSWORD:-password}@''${BEAVER__SAPPHIRE__SQL__HOST:-localhost}:''${BEAVER__SAPPHIRE__SQL__PORT:-34000}/database"
            '';
          };

          package = pkgs.mkShell {
            name = "package";

            packages = [
              python
              task
              coreutils
              poetry
              cacert
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          runtime = pkgs.mkShell {
            name = "runtime";

            packages = [
              node
              python
              poetry
              cacert
              openssl
              tini
              su-exec
            ];

            EXTRAPYTHONPATH = "${python}/${python.sitePackages}";
            LD_LIBRARY_PATH = lib.makeLibraryPath [openssl];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          template = pkgs.mkShell {
            name = "template";

            packages = [
              task
              coreutils
              copier
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          lint = pkgs.mkShell {
            name = "lint";

            packages = [
              node
              task
              coreutils
              trunk
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          test = pkgs.mkShell {
            name = "test";

            packages = [
              node
              python
              task
              coreutils
              poetry
              cacert
              openssl
            ];

            EXTRAPYTHONPATH = "${python}/${python.sitePackages}";
            LD_LIBRARY_PATH = lib.makeLibraryPath [openssl];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          docs = pkgs.mkShell {
            name = "docs";

            packages = [
              node
              task
              coreutils
            ];

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };
        };
      };
    };
}
