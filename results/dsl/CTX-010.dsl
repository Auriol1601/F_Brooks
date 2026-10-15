workspace "Système de réservation" {

    model {
        client = person "Client"
        applicationReservation = softwareSystem "Application de réservation"
        servicePaiement = softwareSystem "Service de paiement"

        client -> applicationReservation "Utilise pour effectuer des réservations"
        applicationReservation -> servicePaiement "Utilise pour traiter les paiements"
    }

    views {
        systemContext applicationReservation "SystemContext" {
            include *
            autoLayout
        }
    }
}
