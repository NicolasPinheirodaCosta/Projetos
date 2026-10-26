class CurrencyExchange:
    def __init__(self, exchange_rates):
        self.exchange_rates = exchange_rates

    def budget_exchange(self): #list of monetary units for exchange possible. references: dollar
        monetary_unit = {
            "USD": 1.0, #dollar
            "EUR": 0.85, #Euro
            "GBP": 0.75, #british pound
            "JPY": 110.0, #yen
            "BRL": 5.0 #brazilian real
        }
        return monetary_unit

    def exchange_money(self): #try to exchange money using any monetary unit available
        exchange_rate = input("Which currency do you want to exchange? (USD, EUR, GBP, JPY, BRL): ")
        if exchange_rate in self.monetary_unit:
            amount = float(input(f"How much {exchange_rate} do you want exchange?"))
            target_currency = input("Which currency do you want to convert to? (USD, EUR, GBP, JPY, BRL): ")
            target_currency_rate = self.monetary_unit.get(target_currency)

            monetary_exchange = (amount / self.monetary_unit[exchange_rate]) *  target_currency_rate
            return(f"Congrats! You exchanged {amount} {exchange_rate} for {monetary_exchange:.2f} {target_currency}")