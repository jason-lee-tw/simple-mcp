from memory_management.service import MemoryManagementService


def main():
    memory = MemoryManagementService()

    memory.save_memory('testing is using Pytest')
    memory.save_memory('This project is using python')
    memory.save_memory('I know Tyepscript')

    result = memory.get_memory('testing')
    print(f'Result: {result}')


if __name__ == "__main__":
    main()
