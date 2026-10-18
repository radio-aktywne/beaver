{
  inputs = {
    flake-parts = {
      url = "github:hercules-ci/flake-parts";
    };

    multiverse = {
      url = "github:fzakaria/nixpkgs-multiverse";
    };

    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixos-26.05";
    };
  };

  outputs = inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      flake = {
        overlays = {
          default = final: prev: {
            # Add multiverse as an attribute
            multiverse = inputs.multiverse.lib.mkMultiverse {
              config = {
                # Allow packages with non-free licenses
                allowUnfree = true;
              };

              system = final.stdenv.hostPlatform.system;
            };
          };
        };
      };

      # Sensible defaults
      systems = [
        "x86_64-linux"
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
        nix = pkgs.nix;
        node = pkgs.nodejs_26;
        python = pkgs.python314;
        nh = pkgs.nh;
        nil = pkgs.nil;
        task = pkgs.go-task;
        coreutils = pkgs.coreutils;
        trunk = pkgs.trunk-io;
        uv = pkgs.uv;
        cacert = pkgs.cacert;
        prisma-engines = pkgs.multiverse.versions.prisma-engines."5.21.0";
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
          };

          overlays = [
            # Use default overlay
            inputs.self.overlays.default
          ];
        };

        # Set which formatter should be used
        formatter = pkgs.alejandra;

        # Define multiple development shells for different purposes
        devShells = {
          default = pkgs.mkShell {
            name = "dev";

            packages = [
              nix
              node
              python
              nh
              nil
              task
              coreutils
              trunk
              uv
              cacert
              prisma-engines
              openssl
              usql
            ];

            PKG_CONFIG_PATH = "${openssl.dev}/lib/pkgconfig";
            PRISMA_FMT_BINARY = "${prisma-engines}/bin/prisma-fmt";
            PRISMA_INTROSPECTION_ENGINE_BINARY = "${prisma-engines}/bin/introspection-engine";
            PRISMA_QUERY_ENGINE_BINARY = "${prisma-engines}/bin/query-engine";
            PRISMA_QUERY_ENGINE_LIBRARY = "${prisma-engines}/lib/libquery_engine.node";
            PRISMA_SCHEMA_ENGINE_BINARY = "${prisma-engines}/bin/schema-engine";
            UV_PYTHON = python;
            UV_PYTHON_PREFERENCE = "only-system";

            shellHook = ''
              export TMPDIR=/tmp
              export PRISMA_DB_URL="postgres://user:''${BEAVER__SAPPHIRE__SQL__PASSWORD:-password}@''${BEAVER__SAPPHIRE__SQL__HOST:-localhost}:''${BEAVER__SAPPHIRE__SQL__PORT:-10510}/database"
            '';
          };

          runtime = pkgs.mkShell {
            name = "runtime";

            packages = [
              node
              python
              uv
              cacert
              prisma-engines
              openssl
              tini
              su-exec
            ];

            PKG_CONFIG_PATH = "${openssl.dev}/lib/pkgconfig";
            PRISMA_FMT_BINARY = "${prisma-engines}/bin/prisma-fmt";
            PRISMA_INTROSPECTION_ENGINE_BINARY = "${prisma-engines}/bin/introspection-engine";
            PRISMA_QUERY_ENGINE_BINARY = "${prisma-engines}/bin/query-engine";
            PRISMA_QUERY_ENGINE_LIBRARY = "${prisma-engines}/lib/libquery_engine.node";
            PRISMA_SCHEMA_ENGINE_BINARY = "${prisma-engines}/bin/schema-engine";
            UV_PYTHON = python;
            UV_PYTHON_PREFERENCE = "only-system";

            shellHook = ''
              export TMPDIR=/tmp
            '';
          };

          lint = pkgs.mkShell {
            name = "lint";

            packages = [
              nix
              node
              python
              task
              coreutils
              trunk
              uv
              cacert
              prisma-engines
            ];

            PKG_CONFIG_PATH = "${openssl.dev}/lib/pkgconfig";
            PRISMA_FMT_BINARY = "${prisma-engines}/bin/prisma-fmt";
            PRISMA_INTROSPECTION_ENGINE_BINARY = "${prisma-engines}/bin/introspection-engine";
            PRISMA_QUERY_ENGINE_BINARY = "${prisma-engines}/bin/query-engine";
            PRISMA_QUERY_ENGINE_LIBRARY = "${prisma-engines}/lib/libquery_engine.node";
            PRISMA_SCHEMA_ENGINE_BINARY = "${prisma-engines}/bin/schema-engine";
            UV_PYTHON = python;
            UV_PYTHON_PREFERENCE = "only-system";

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
              uv
              cacert
              prisma-engines
              openssl
            ];

            PKG_CONFIG_PATH = "${openssl.dev}/lib/pkgconfig";
            PRISMA_FMT_BINARY = "${prisma-engines}/bin/prisma-fmt";
            PRISMA_INTROSPECTION_ENGINE_BINARY = "${prisma-engines}/bin/introspection-engine";
            PRISMA_QUERY_ENGINE_BINARY = "${prisma-engines}/bin/query-engine";
            PRISMA_QUERY_ENGINE_LIBRARY = "${prisma-engines}/lib/libquery_engine.node";
            PRISMA_SCHEMA_ENGINE_BINARY = "${prisma-engines}/bin/schema-engine";
            UV_PYTHON = python;
            UV_PYTHON_PREFERENCE = "only-system";

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
