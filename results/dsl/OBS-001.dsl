workspace "Application de notes" {

    model {
        utilisateur = person "Utilisateur"

        applicationNotes = softwareSystem "Application de notes" {
            interfaceSaisie = container "Interface de saisie"
            processusPrincipal = container "Processus principal"
        }

        utilisateur -> interfaceSaisie "Rédige et consulte ses notes"
        interfaceSaisie -> processusPrincipal "Communique avec"
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
