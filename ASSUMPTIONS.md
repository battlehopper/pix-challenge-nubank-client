## Premissas

1. Endpoints disponíveis:
   * `GET /keys/<pix_key>` → 200 JSON | 404
   * `POST /transactions`  → 201 JSON
2. Montante é inteiro em centavos para evitar ponto flutuante.
3. Sem autenticação ou TLS: será abordado no pair-programming.
