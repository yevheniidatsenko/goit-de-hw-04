import os
import time
import threading
from multiprocessing import Process, Queue
from queue import Queue as ThreadQueue
from colorama import Fore, Style, init

# Initialize Colorama for colored text in the console
init(autoreset=True)

# Function to search for keywords in a file
def search_keywords_in_file(file_path, keywords, result_dict, identifier):
    """
    Search for keywords in a text file.

    Parameters:
    - file_path: path to the file
    - keywords: list of keywords to search for
    - result_dict: dictionary to store the results
    - identifier: unique identifier for the thread or process

    Result:
    - Updates result_dict by adding found keywords and corresponding files.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Message indicating successful file reading
            print(f"{Fore.GREEN}{identifier}: File '{
                  file_path}' read.{Style.RESET_ALL}")
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    if keyword not in result_dict:
                        result_dict[keyword] = []
                    result_dict[keyword].append(file_path)
    except Exception as e:
        # Error message
        print(f"{Fore.RED}{identifier}: Error reading file {
              file_path}: {e}{Style.RESET_ALL}")

# Function to process files using threads
def threading_approach(file_paths, keywords):
    """
    Search for keywords in text files using threads.

    Parameters:
    - file_paths: list of files
    - keywords: list of keywords to search for

    Result:
    - Returns a dictionary with keywords and corresponding files.
    """
    threads = []
    results = ThreadQueue()  # Thread queue for storing results
    results_dict = {}

    def worker(file_paths_chunk, thread_id):
        """
        Worker function for threads.
        Searches for keywords in a chunk of files.
        """
        local_results = {}
        for file_path in file_paths_chunk:
            search_keywords_in_file(
                file_path, keywords, local_results, f"Thread-{thread_id}")
        results.put(local_results)

    # Divide files among threads
    num_threads = min(len(file_paths), 3)  # Limit threads to 3
    chunk_size = len(file_paths) // num_threads
    for i in range(num_threads):
        chunk = file_paths[i * chunk_size:(i + 1) * chunk_size] if i < num_threads - 1 else file_paths[i * chunk_size:]
        thread = threading.Thread(target=worker, args=(chunk, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Combine results from threads
    while not results.empty():
        partial_result = results.get()
        for keyword, paths in partial_result.items():
            if keyword not in results_dict:
                results_dict[keyword] = []
            results_dict[keyword].extend(paths)

    return results_dict

# Global function for multiprocessing workers
def multiprocessing_worker(file_paths_chunk, keywords, queue, process_id):
    """
    Worker function for processes.
    Searches for keywords in a chunk of files and passes results via a queue.
    """
    local_results = {}
    for file_path in file_paths_chunk:
        search_keywords_in_file(file_path, keywords,
                                local_results, f"Process-{process_id}")
    queue.put(local_results)

# Function to process files using multiprocessing
def multiprocessing_approach(file_paths, keywords):
    """
    Search for keywords in text files using multiprocessing.

    Parameters:
    - file_paths: list of files
    - keywords: list of keywords to search for

    Result:
    - Returns a dictionary with keywords and corresponding files.
    """
    processes = []
    queue = Queue()  # Queue for results
    results_dict = {}

    # Divide files among processes
    num_processes = min(len(file_paths), 3)  # Limit processes to 3
    chunk_size = len(file_paths) // num_processes
    for i in range(num_processes):
        chunk = file_paths[i * chunk_size:(i + 1) * chunk_size] if i < num_processes - 1 else file_paths[i * chunk_size:]
        process = Process(target=multiprocessing_worker,
                          args=(chunk, keywords, queue, i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    # Combine results from processes
    while not queue.empty():
        partial_result = queue.get()
        for keyword, paths in partial_result.items():
            if keyword not in results_dict:
                results_dict[keyword] = []
            results_dict[keyword].extend(paths)

    return results_dict

# Main function of the program
def main():
    """
    Main function that runs threading and multiprocessing approaches
    to search for keywords in text files.
    """
    # Keywords to search for
    keywords = ["error", "keyword", "test"]

    # Find files with .txt extension
    file_paths = [f for f in os.listdir(".") if f.endswith(".txt")]
    print(f"{Fore.YELLOW}Found text files: {file_paths}{Style.RESET_ALL}\n")

    if not file_paths:
        print(f"{Fore.RED}No .txt files found. Exiting.{Style.RESET_ALL}")
        return

    # Threading approach
    print(f"{Fore.MAGENTA}--- Threading Approach ---{Style.RESET_ALL}")
    start_time = time.time()
    threading_results = threading_approach(file_paths, keywords)
    threading_time = time.time() - start_time
    print(f"{Fore.MAGENTA}Threading results:{Style.RESET_ALL}")
    for keyword, files in threading_results.items():
        print(f"{Fore.LIGHTCYAN_EX}{keyword}: {files}")
    print(f"{Fore.YELLOW}Time taken: {
          threading_time:.2f} seconds{Style.RESET_ALL}\n")

    # Multiprocessing approach
    print(f"{Fore.MAGENTA}--- Multiprocessing Approach ---{Style.RESET_ALL}")
    start_time = time.time()
    multiprocessing_results = multiprocessing_approach(file_paths, keywords)
    multiprocessing_time = time.time() - start_time
    print(f"{Fore.MAGENTA}Multiprocessing results:{Style.RESET_ALL}")
    for keyword, files in multiprocessing_results.items():
        print(f"{Fore.LIGHTCYAN_EX}{keyword}: {files}")
    print(f"{Fore.YELLOW}Time taken: {
          multiprocessing_time:.2f} seconds{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()