workspace "Application de paiement mobile" {

    model {
        client = person "Client"
        
        applicationPaiement = softwareSystem "Application de paiement mobile"
        prestatairePaiement = softwareSystem "Prestataire de paiement"

        client -> applicationPaiement "Paye ses factures"
        applicationPaiement -> prestatairePaiement "Utilise pour les paiements"
    }

    views {
        systemContext applicationPaiement "SystemContext" {
            include *
            autoLayout
        }
    }
}
