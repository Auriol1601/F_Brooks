workspace "Application RH" {

    model {
        employe = person "Employé"
        systemeRHCentral = softwareSystem "Système RH central"

        appRH = softwareSystem "Application RH" {
            appWeb = container "Application web"
            db = container "Base de données"
        }

        employe -> appWeb "Utilise"
        appWeb -> db "Lit et écrit"
        appWeb -> systemeRHCentral "Récupère certaines informations"
    }

    views {
        systemContext appRH "SystemContext" {
            include *
            autoLayout
        }
        container appRH "Containers" {
            include *
            autoLayout
        }
    }
}
