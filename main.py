import argparse
from pathlib import Path

from installer.generator import preview_config, write_output
from installer.persistence import load_config, save_config
from installer.validator import validation_warnings, validate_config
from installer.wizard import ask_yes_no, collect_user_input, edit_review_config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de configuração do Homepage")
    parser.add_argument("--output", default="generated", help="Diretório para exportar os arquivos finais")
    parser.add_argument("--skip-preview", action="store_true", help="Pula a revisão final antes da exportação")
    parser.add_argument("--state-file", default=".homepage-installer-state.json", help="Arquivo de estado para reabrir ou continuar o projeto")
    parser.add_argument("--resume", action="store_true", help="Carrega a última configuração salva e continua o fluxo")
    args = parser.parse_args()

    state_file = Path(args.state_file)
    if args.resume and state_file.exists():
        config = load_config(str(state_file))
        print(f"Configuração carregada de {state_file}")
    else:
        config = collect_user_input()

    errors = validate_config(config)

    if errors:
        print("\nErros de validação:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    warnings = validation_warnings(config)
    if warnings:
        print("\nAvisos importantes:")
        for warning in warnings:
            print(f"- {warning}")

    save_config(config, str(state_file))

    if not args.skip_preview:
        print("\n" + preview_config(config))
        approved = edit_review_config(config)
        if not approved:
            print("Exportação cancelada.")
            raise SystemExit(0)

    write_output(config, output_dir=args.output)
    save_config(config, str(state_file))
    print("\nDica: copie a pasta config do diretório de exportação para o diretório config do seu Homepage.")
