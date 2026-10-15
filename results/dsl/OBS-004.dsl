workspace "Application de réservation" {

    model {
        client = person "Client"
        appReservation = softwareSystem "Application de réservation"
        servicePaiement = softwareSystem "Service de paiement"
        serviceNotification = softwareSystem "Service de notification"

        client -> appReservation "Utilise"
        appReservation -> servicePaiement "Utilise"
        appReservation -> serviceNotification "Utilise"
    }

    views {
        systemContext appReservation "SystemContext" {
            include *
            autoLayout
        }
    }
}
