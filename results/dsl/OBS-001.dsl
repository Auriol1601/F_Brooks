workspace "Application de notes" {

    model {
        utilisateur = person "Utilisateur"

        syncService = softwareSystem "Service de synchronisation" "api.sync.example.com"

        applicationNotes = softwareSystem "Application de notes" {
            interfaceSaisie = container "Interface de saisie" "" "Electron Renderer (HTML/JS)"
            processusPrincipal = container "Processus principal" "" "Electron Main (Node.js)"
            stockageLocal = container "Stockage local" "" "IndexedDB"
        }

        utilisateur -> interfaceSaisie "Rédige et consulte ses notes"
        interfaceSaisie -> processusPrincipal "Communique (IPC)"
        interfaceSaisie -> stockageLocal "Lit et écrit les notes"
        processusPrincipal -> syncService "Synchronise les notes"
    }

    views {
        systemContext applicationNotes "SystemContext" {
            include *
            autoLayout
        }
        container applicationNotes "Containers" {
            include *
            autoLayout
        }
    }
}
