workspace "Application de réservation" {

    model {
        client = person "Client"
        applicationReservation = softwareSystem "Application de réservation"
        servicePaiement = softwareSystem "Service de paiement"

        client -> applicationReservation "Utilise"
        applicationReservation -> servicePaiement "Utilise"
    }

    views {
        systemContext applicationReservation "SystemContext" {
            include *
            autoLayout
        }
    }
}
