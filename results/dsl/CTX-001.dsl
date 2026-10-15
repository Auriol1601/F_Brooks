workspace "Plateforme de gestion des congés" {

    model {
        employe = person "Employé"
        serviceRH = person "Service RH"
        plateformeConges = softwareSystem "Plateforme de gestion des congés"

        employe -> plateformeConges "Soumet des demandes de congés"
        serviceRH -> plateformeConges "Reçoit et valide les demandes"
    }

    views {
        systemContext plateformeConges "SystemContext" {
            include *
            autoLayout
        }
    }
}
