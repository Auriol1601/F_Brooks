workspace "Application RH" {

    model {
        employe = person "Employé"
        appRH = softwareSystem "Application RH"
        systemeRHCentral = softwareSystem "Système RH central"

        employe -> appRH "Utilise"
        appRH -> systemeRHCentral "Récupère certaines informations"
    }

    views {
        systemContext appRH "SystemContext" {
            include *
            autoLayout
        }
    }
}
