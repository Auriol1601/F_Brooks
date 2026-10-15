workspace "Plateforme de gestion des congés" {

    model {
        employe = person "Employé"
        serviceRH = person "Service RH"

        plateformeConges = softwareSystem "Plateforme de gestion des congés" {
            appWeb = container "Application web"
            api = container "API"
            baseDeDonnees = container "Base de données"
        }

        employe -> appWeb "Utilise"
        serviceRH -> appWeb "Utilise"
        appWeb -> api "Appelle"
        api -> baseDeDonnees "Lit et écrit les demandes"
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
