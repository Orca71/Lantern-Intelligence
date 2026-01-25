from tokens_storage import get_tokens

auth_code = input("Paste your authorization code: ")
tokens = get_tokens(auth_code)

print("\nTokens received:")
print(tokens)
