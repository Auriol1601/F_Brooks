workspace "Application de réservation" {

    model {
        client = person "Client"
        applicationReservation = softwareSystem "Application de réservation"
        servicePaiement = softwareSystem "Service de paiement"
        serviceNotification = softwareSystem "Service de notification"
        serviceCartographie = softwareSystem "Service de cartographie"

        client -> applicationReservation "Utilise"
        applicationReservation -> servicePaiement "Utilise"
        applicationReservation -> serviceNotification "Utilise"
        applicationReservation -> serviceCartographie "Utilise"
    }

    views {
        systemContext applicationReservation "SystemContext" {
            include *
            autoLayout
        }
    }
}
