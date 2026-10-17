import { App } from "antd";

/** Messages de retour utilisateur (succès / erreur de l'API) via le contexte antd. */
export function useFeedback() {
  const { message } = App.useApp();
  return {
    success: (content: string) => message.success(content),
    // ApiError porte le message fonctionnel du backend (ex : « Une étagère nommée 'Cave' existe déjà »)
    error: (error: unknown) => message.error(error instanceof Error ? error.message : "Erreur inattendue"),
  };
}
