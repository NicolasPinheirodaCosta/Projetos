class CurrencyExchange:
    def __init__(self, exchange_rates):
        self.exchange_rates = exchange_rates
 
    def exchange_money (self):
        
    
        unite_budget = {
            "USD": 1,
            "EUR": 1.12,
            "BRL": 0.20,
            "GBP": 1.34,
            "YEN": 0.0063}

        try:
            ask = input("Would you like to exchange your money? (USD, EUR, BRL, GBP, YEN): ")
            if ask in unite_budget:
                exchange_rate = unite_budget[ask.upper()]
            else:
                raise ValueError("Invalid currency. Please choose from USD, EUR, BRL, GBP, or YEN.")    
            budget = float(input("What's your budget? "))
            if budget < 0:
                raise ValueError("Budget cannot be negative.")
            if not isinstance(budget, (int, float)):
                raise ValueError("Budget must be a number.")
        except ValueError as e:
            print(f"Error: {e}")

        finally:
            if budget and exchange_rate:
                exchange = round(budget / exchange_rate, 2)
                print(f"Your exchanged amount is: {exchange} {ask.upper()}")

currency = CurrencyExchange({})
currency.exchange_money()