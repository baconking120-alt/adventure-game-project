def print_welcome(name: str, width: int) -> None:
    message = f"Hello, {name}!"
    print(f"{message:^{width}}")
def print_shop_menu(item1Name: str, item1Price: float, item2Name: str, item2Price: float) -> None:
    border = "/" + "-" * 22 + "\\"
    print(border)
    print(f"| {item1Name:<12} ${item1Price:>7.2f} |")
    print(f"| {item2Name:<12} ${item2Price:>7.2f} |")
    print("/" + "-" * 22 + "\\")
print_welcome("Diego", 24)
print_welcome("Wade", 34)
print_shop_menu("Bread", 20, "cheese", 15)
print_shop_menu("juice", 5.23, "cake", 12.33)
