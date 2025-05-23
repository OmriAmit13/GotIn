// Test data for results.html
const testData = [
    {
        server: "Server 1",
        status: "success",
        data: {
            isAccepted: "קבלה",
            url: "https://university1.edu/application",
            message: "ברכותינו! התקבלת למסלול המבוקש"
        }
    },
    {
        server: "Server 2",
        status: "success",
        data: {
            isAccepted: "דחייה",
            url: "https://university2.edu/status",
            message: "לצערנו, לא עמדת בתנאי הקבלה"
        }
    },
    {
        server: "Server 3",
        status: "success",
        data: {
            isAccepted: "רשימת המתנה",
            url: "https://university3.edu/waitlist",
            message: "" // Empty message won't be displayed
        }
    },
    {
        server: "Server 4",
        status: "success",
        data: {
            isAccepted: "קבלה",
            url: "https://university4.edu/accepted",
            message: "     " // Whitespace-only message won't be displayed
        }
    },
    {
        server: "Server 5",
        status: "error", // This result won't be displayed at all
        error: "Server timeout - please try again later"
    }
];

// Function to set test data in localStorage
function setTestData() {
    localStorage.setItem('resultData', JSON.stringify(testData));
    console.log('Test data has been set in localStorage');
}

// Instructions
console.log('To use this test script:');
console.log('1. Run setTestData() in the console');
console.log('2. Refresh the page to see the results');

// Automatically set the data when the script is loaded
setTestData();
