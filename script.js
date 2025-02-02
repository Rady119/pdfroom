// Updated script.js
const API_BASE_URL = "https://pdftool-l8hx.onrender.com"; // استبدلها بالرابط الصحيح لخادمك


// PDF to Word Conversion
document.getElementById("convertPdfToWord").addEventListener("click", async () => {
    const pdfFile = document.getElementById("pdfFile").files[0];
    if (!pdfFile) {
        alert("يرجى اختيار ملف PDF");
        return;
    }

    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
        const response = await fetch(`${API_BASE_URL}/convert-pdf-to-word`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`الخادم أرجع الحالة ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        if (data.download_link && data.filename) {
            const link = document.getElementById("downloadPdfToWord");
            link.href = `${API_BASE_URL}/${data.download_link}`;
            link.download = data.filename; // تعيين اسم الملف الصحيح
            link.style.display = "inline-block";
        } else {
            alert("حدث خطأ أثناء التحويل. يرجى المحاولة لاحقاً.");
        }
    } catch (error) {
        console.error("خطأ:", error);
        alert("خطأ: لا يمكن الاتصال بالخادم أو أن الخادم لا يستجيب.");
    }
});
