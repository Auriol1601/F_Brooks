workspace "Plateforme de gestion des congés" {

    model {
        employe = person "Employé"
        serviceRH = person "Service RH"
        plateforme = softwareSystem "Plateforme de gestion des congés"

        employe -> plateforme "Soumet des demandes de congés"
        plateforme -> serviceRH "Transmet les demandes de congés"
        serviceRH -> plateforme "Reçoit et valide les demandes"
    }

    views {
        systemContext plateforme "SystemContext" {
            include *
            autoLayout
        }
    }
}
