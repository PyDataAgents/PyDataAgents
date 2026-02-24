import ollama


class ModelUtils:
    @staticmethod
    def get_ollama_client(endpoint: str | None):
        if endpoint is None or str(endpoint).strip() == "":
            return ollama.Client()
        return ollama.Client(host=endpoint)

    @staticmethod
    def _extract_model_names(response) -> set[str]:
        names: set[str] = set()
        for model_entry in getattr(response, "models", []):
            model_name = getattr(model_entry, "model", None)
            if model_name is not None and str(model_name).strip() != "":
                names.add(str(model_name))
        return names

    @staticmethod
    def _model_candidates(model: str) -> set[str]:
        model_name = str(model).strip()
        if model_name == "":
            return set()
        candidates = {model_name}
        if ":" not in model_name:
            candidates.add(model_name + ":latest")
        return candidates

    @staticmethod
    def list_ollama_models(endpoint: str | None) -> set[str]:
        client = ModelUtils.get_ollama_client(endpoint)
        response = client.list()
        return ModelUtils._extract_model_names(response)

    @staticmethod
    def ensure_ollama_model_available(model: str, endpoint: str | None) -> None:
        model_name = str(model).strip()
        if model_name == "":
            raise RuntimeError("Configured Ollama model must not be empty.")

        endpoint_display = endpoint if endpoint is not None and str(endpoint).strip() != "" else "http://localhost:11434"
        client = ModelUtils.get_ollama_client(endpoint)
        candidates = ModelUtils._model_candidates(model_name)
        install_cmd = "ollama pull " + model_name

        try:
            installed_before = ModelUtils._extract_model_names(client.list())
        except Exception as exc:
            raise RuntimeError(
                "Failed to list Ollama models at endpoint '"
                + endpoint_display
                + "' while checking model '"
                + model_name
                + "'. Manual command: "
                + install_cmd
                + ". Root cause: "
                + str(exc)
            ) from exc

        if len(candidates.intersection(installed_before)) > 0:
            return

        try:
            client.pull(model_name, stream=False)
        except Exception as exc:
            available_models = ", ".join(sorted(installed_before)) if len(installed_before) > 0 else "none"
            raise RuntimeError(
                "Ollama model '"
                + model_name
                + "' is missing at endpoint '"
                + endpoint_display
                + "' and automatic pull failed. Available models: "
                + available_models
                + ". Manual command: "
                + install_cmd
                + ". Root cause: "
                + str(exc)
            ) from exc

        try:
            installed_after = ModelUtils._extract_model_names(client.list())
        except Exception as exc:
            raise RuntimeError(
                "Model pull for '"
                + model_name
                + "' was triggered, but post-pull validation failed at endpoint '"
                + endpoint_display
                + "'. Manual command: "
                + install_cmd
                + ". Root cause: "
                + str(exc)
            ) from exc

        if len(candidates.intersection(installed_after)) > 0:
            return

        available_models = ", ".join(sorted(installed_after)) if len(installed_after) > 0 else "none"
        raise RuntimeError(
            "Ollama model '"
            + model_name
            + "' is still unavailable after automatic pull at endpoint '"
            + endpoint_display
            + "'. Available models: "
            + available_models
            + ". Manual command: "
            + install_cmd
            + "."
        )
