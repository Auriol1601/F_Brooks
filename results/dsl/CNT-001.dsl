workspace "Plateforme de gestion des congés" {

    model {
        employe = person "Employé"
        serviceRH = person "Service RH"

        plateformeConges = softwareSystem "Plateforme de gestion des congés" {
            appWeb = container "Application web"
            api = container "API"
            bdd = container "Base de données"
        }

        employe -> appWeb "Soumet des demandes de congés"
        serviceRH -> appWeb "Reçoit et valide les demandes"
        appWeb -> api "Appelle"
        api -> bdd "Lit et écrit les demandes"
    }

    views {
        systemContext plateformeConges "SystemContext" {
            include *
            autoLayout
        }
        container plateformeConges "Containers" {
            include *
            autoLayout
        }
    }
}
