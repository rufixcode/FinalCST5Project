using System;
using MySql.Data.MySqlClient;

class CheckBookAvailability
{
    static void Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.WriteLine("Error: No book ID provided.");
            return;
        }

        int bookId;
        if (!int.TryParse(args[0], out bookId))
        {
            Console.WriteLine("Error: Invalid book ID.");
            return;
        }

        string connStr = "server=localhost;user=root;database=LibraryDb;port=3306;password=";

        using (var conn = new MySqlConnection(connStr))
        {
            try
            {
                conn.Open();

                // Check if the book is borrowed
                string query = "SELECT COUNT(*) FROM borrowed_books WHERE book_id = @bookId";
                MySqlCommand cmd = new MySqlCommand(query, conn);
                cmd.Parameters.AddWithValue("@bookId", bookId);

                int count = Convert.ToInt32(cmd.ExecuteScalar());

                Console.WriteLine(count == 0 ? "Available" : "Borrowed");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Error: " + ex.Message);
                Environment.Exit(1);
            }
        }
    }
}
