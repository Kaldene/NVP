using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using NAudio.Wave;

namespace AudioAnalyticsClient
{
    class Program
    {
        private static WaveInEvent? _waveIn;
        private static WaveFileWriter? _writer;
        private static string _tempFilePath = "current_shift_record.wav";

        static async Task Main(string[] args)
        {
            Console.WriteLine("=== MVP Audio Client ===");
            Console.WriteLine("Нажми [Enter] для начала записи смены...");
            Console.ReadLine();

            StartRecording();

            Console.WriteLine("Идет запись... Нажми [Enter] для завершения и отправки на сервер.");
            Console.ReadLine();

            StopRecording();
            await SendAudioAsync();
            
            Console.WriteLine("\nГотово. Нажми любую клавишу для выхода.");
            Console.ReadKey();
        }

        static void StartRecording()
        {
            // Настраиваем качество записи (44100 Гц, Моно)
            _waveIn = new WaveInEvent
            {
                WaveFormat = new WaveFormat(44100, 1) 
            };

            // Событие, которое срабатывает, когда микрофон ловит звук
            _waveIn.DataAvailable += (sender, e) =>
            {
                _writer?.Write(e.Buffer, 0, e.BytesRecorded);
            };

            // Создаем файл для записи
            _writer = new WaveFileWriter(_tempFilePath, _waveIn.WaveFormat);
            
            // Начинаем слушать микрофон
            _waveIn.StartRecording();
        }

        static void StopRecording()
        {
            _waveIn?.StopRecording();
            _waveIn?.Dispose();
            _waveIn = null;

            // КРИТИЧЕСКИ ВАЖНО: Закрываем файл аудио, чтобы он сохранился на диск 
            // и разблокировался для чтения перед отправкой на сервер.
            _writer?.Dispose();
            _writer = null;
        }

        static async Task SendAudioAsync()
        {
            Console.WriteLine("\nОтправляем аудиофайл на бэкенд...");

            try
            {
                using var client = new HttpClient();
                client.DefaultRequestHeaders.Add("x-club-secret", "super_secret_club_123");

                using var form = new MultipartFormDataContent();
        
                // 1. ЖЕСТКИЙ ФИКС КАВЫЧЕК: принудительно удаляем их из заголовка boundary
                var boundary = form.Headers.ContentType?.Parameters.FirstOrDefault(p => p.Name == "boundary");
                if (boundary != null && boundary.Value != null)
                {
                    boundary.Value = boundary.Value.Replace("\"", "");
                }

                // 2. ФИКС ПОТОКА: читаем файл как массив байтов, чтобы избежать ошибки Chunked Encoding
                byte[] fileBytes = await File.ReadAllBytesAsync(_tempFilePath);
                using var fileContent = new ByteArrayContent(fileBytes);
        
                // 3. Явно указываем Python-серверу, что это аудиофайл
                fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");

                // Имя поля "file" должно совпадать с UploadFile = File(...) в FastAPI
                form.Add(fileContent, "file", "current_shift_record.wav");
                
                int currentEmployeeId = 1;
                string serverUrl = $"http://127.0.0.1:8000/api/v1/mobile/upload?employee_id={currentEmployeeId}";
                
                // ВАЖНО: Добавляем сам POST-запрос, которого не хватало!
                var response = await client.PostAsync(serverUrl, form);
                
                var responseText = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine($"Успех! Сервер ответил: {responseText}");
                    Console.ResetColor();
                }
                else
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"Ошибка {response.StatusCode}: {responseText}");
                    Console.ResetColor();
                }
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"Ошибка при отправке: {ex.Message}");
                Console.ResetColor();
            }
        }
    }
}