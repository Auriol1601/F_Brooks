workspace "Application de paiement mobile" {

    model {
        client = person "Client"
        applicationPaiement = softwareSystem "Application de paiement mobile"

        client -> applicationPaiement "Utilise pour payer leurs factures"
    }

    views {
        systemContext applicationPaiement "SystemContext" {
            include *
            autoLayout
        }
    }
}
