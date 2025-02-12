using System;
using System.Collections.Generic;
using System.IO;

namespace FileHelper
{
    class Program
    {
        /// <summary>
        /// Retrieves file paths of all files in the specified folder that contain a given keyword in their name and match the specified file type.
        /// </summary>
        /// <param name="folderPath">Path of the folder to search in</param>
        /// <param name="fileKeyword">Keyword that the filename should contain</param>
        /// <param name="fileExtension">File extension to filter by</param>
        /// <returns>List of matching file paths</returns>
        static List<string> GetFiles(string folderPath, string fileKeyword, string fileExtension)
        {
            List<string> fileList = new List<string>();
            try
            {
                string searchPattern = $"*{fileKeyword}*{fileExtension}";
                string[] files = Directory.GetFiles(folderPath, searchPattern); // Search using wildcard pattern
                Console.WriteLine("Total {0} items found. Displaying matching files:", files.Length);
                
                foreach (string file in files)
                {
                    fileList.Add(file);
                    Console.WriteLine(file);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("An error occurred: {0}", e.Message);
            }

            return fileList;
        }

        static void Main(string[] args)
        {
            var files = GetFiles(@"F:\Photos\Camera\CapturedMedia\2014", "", ".JPG");
            Console.WriteLine("Search completed. Press any key to exit...");
            Console.ReadKey();
        }
    }
}