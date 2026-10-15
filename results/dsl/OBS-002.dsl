workspace "Application de paiement mobile" {

    model {
        client = person "Client"
        applicationPaiementMobile = softwareSystem "Application de paiement mobile"

        client -> applicationPaiementMobile "Paie ses factures"
    }

    views {
        systemContext applicationPaiementMobile "SystemContext" {
            include *
            autoLayout
        }
    }
}
