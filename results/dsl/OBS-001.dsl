workspace "Application de notes" {

    model {
        utilisateur = person "Utilisateur" "Rédige et consulte ses notes"

        applicationNotes = softwareSystem "Application de notes" {
            processusPrincipal = container "Processus principal"
            interfaceSaisie = container "Interface de saisie"
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
