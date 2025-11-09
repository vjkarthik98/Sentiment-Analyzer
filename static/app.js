document.addEventListener("DOMContentLoaded", () => {
    const textInput = document.getElementById("text-input");
    const analyzeButton = document.getElementById("analyze-button");
    const resultLabel = document.getElementById("result-label");
    const resultScore = document.getElementById("result-score");

    // --- IMPORTANT ---
    // When we run locally, the API is on port 5000
    // When we deploy, it will be on a different URL.
    // We will update this URL in Phase 4.
    const API_URL = "http://127.0.0.1:5000/analyze"; 
    // const API_URL = "YOUR_AWS_URL_GOES_HERE/analyze"; // Deployed

    analyzeButton.addEventListener("click", async () => {
        const text = textInput.value;
        if (!text) {
            alert("Please enter some text to analyze.");
            return;
        }

        // Show loading state
        resultLabel.textContent = "Analyzing...";
        resultScore.textContent = "";
        resultLabel.className = ""; // Reset color

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text: text }),
            });

            if (!response.ok) {
                // Handle API errors (like 400, 500)
                const errorData = await response.json();
                throw new Error(errorData.message || "Something went wrong");
            }

            const data = await response.json();

            // Update the UI with results
            resultLabel.textContent = data.label;
            resultScore.textContent = `Confidence: ${(data.score * 100).toFixed(2)}%`;

            // Add color class
            if (data.label === "POSITIVE") {
                resultLabel.className = "positive";
            } else {
                resultLabel.className = "negative";
            }

        } catch (error) {
            // Handle network errors or errors from the 'throw'
            resultLabel.textContent = "Error";
            resultScore.textContent = error.message;
            resultLabel.className = "negative";
        }
    });
});