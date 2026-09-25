workspace "Test F. Brooks" "Test de démarrage Structurizr Lite" {
    model {
        user = person "Utilisateur"
        softwareSystem = softwareSystem "Système F. Brooks"
        user -> softwareSystem "Utilise"
    }
    views {
        systemContext softwareSystem "SystemContext" {
            include *
            autolayout lr
        }
    }
}
