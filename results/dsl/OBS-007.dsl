workspace "Application RH" {

    model {
        employe = person "Employé"
        systemeRHCentral = softwareSystem "Système RH central"

        applicationRH = softwareSystem "Application RH" {
            applicationWeb = container "Application web"
            baseDeDonnees = container "Base de données"
        }

        employe -> applicationWeb "Utilise"
        applicationWeb -> baseDeDonnees "Lit et écrit"
        applicationWeb -> systemeRHCentral "Récupère certaines informations"
    }

    views {
        systemContext applicationRH "SystemContext" {
            include *
            autoLayout
        }
        container applicationRH "Containers" {
            include *
            autoLayout
        }
    }
}
