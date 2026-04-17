class ConfirmationManager:

    def needs_confirmation(self, action):
        """
        Decide whether an action requires confirmation.
        """
        return action["domain"] == "AP"
        

    def ask(self, action):
        """
        Generate a confirmation question.
        """
        intent = action["fine_intent"]
        vendor = action["payload"].get("vendor")
        amount = action["payload"].get("amount")

        return {
            "status": "confirm_needed",
            "message": f"Do you want to pay {vendor} ${amount}?",
            "intent": intent,
            "action": action,
        }

    def approved(self, action):
        """
        This is called when user says “yes”.
        """
        return {
            "status": "execute",
            "action": action,
            "message": "Confirmed. Executing."
        }
