// =========================================================
// TRAINREADY - MAIN JAVASCRIPT
// =========================================================

let selectedFile = null;

let dataTypeChartInstance = null;
let missingChartInstance = null;
let targetChartInstance = null;


// =========================================================
// DOUGHNUT CHART - PERCENTAGE LABEL PLUGIN
// =========================================================

const percentageLabelsPlugin = {
    id: "percentageLabels",

    afterDatasetsDraw(chart) {
        if (
            chart.config.type !== "doughnut" &&
            chart.config.type !== "pie"
        ) {
            return;
        }

        const ctx = chart.ctx;
        const dataset = chart.data.datasets[0];

        if (!dataset || !dataset.data) {
            return;
        }

        const total = dataset.data.reduce(
            (sum, value) => sum + Number(value || 0),
            0
        );

        if (total <= 0) {
            return;
        }

        const meta = chart.getDatasetMeta(0);

        ctx.save();

        meta.data.forEach((arc, index) => {
            const value = Number(dataset.data[index] || 0);

            if (value <= 0) {
                return;
            }

            const percentage = (value / total) * 100;

            // Hide labels for very small slices
            if (percentage < 3) {
                return;
            }

            const angle =
                (arc.startAngle + arc.endAngle) / 2;

            const radius =
                (arc.innerRadius + arc.outerRadius) / 2;

            const x =
                arc.x + Math.cos(angle) * radius;

            const y =
                arc.y + Math.sin(angle) * radius;

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 13px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            ctx.fillText(
                `${percentage.toFixed(1)}%`,
                x,
                y
            );
        });

        ctx.restore();
    }
};


// =========================================================
// PAGE INITIALIZATION
// =========================================================

document.addEventListener("DOMContentLoaded", function () {
    initializeUploadPage();
    initializeResultsPage();
});


// =========================================================
// UPLOAD PAGE
// =========================================================

function initializeUploadPage() {
    const fileInput = document.getElementById("fileInput");
    const dropArea = document.getElementById("dropArea");
    const removeButton = document.getElementById("removeFile");
    const analyzeButton = document.getElementById("analyzeButton");

    const browseButton =
        document.querySelector('label[for="fileInput"]');

    if (!fileInput && !dropArea) {
        return;
    }

    // Browse File button
    if (browseButton && fileInput) {
        browseButton.addEventListener("click", function (event) {
            event.preventDefault();
            fileInput.click();
        });
    }

    // File selection
    if (fileInput) {
        fileInput.addEventListener("change", function (event) {
            const files = event.target.files;

            if (files && files.length > 0) {
                handleSelectedFile(files[0]);
            }
        });
    }

    // Remove file
    if (removeButton) {
        removeButton.addEventListener(
            "click",
            removeSelectedFile
        );
    }

    // Analyze button
    if (analyzeButton) {
        analyzeButton.addEventListener(
            "click",
            analyzeDataset
        );
    }

    // Drag and drop
    if (dropArea) {
        dropArea.addEventListener("dragover", function (event) {
            event.preventDefault();
            dropArea.classList.add("drag-over");
        });

        dropArea.addEventListener("dragleave", function () {
            dropArea.classList.remove("drag-over");
        });

        dropArea.addEventListener("drop", function (event) {
            event.preventDefault();
            dropArea.classList.remove("drag-over");

            const files = event.dataTransfer.files;

            if (files && files.length > 0) {
                handleSelectedFile(files[0]);
            }
        });
    }
}


// =========================================================
// FILE SELECTION
// =========================================================

function handleSelectedFile(file) {
    const allowedExtensions = [
        ".csv",
        ".xlsx",
        ".xls"
    ];

    const fileName = file.name.toLowerCase();

    const isAllowed = allowedExtensions.some(
        extension => fileName.endsWith(extension)
    );

    if (!isAllowed) {
        showMessage(
            "Please select a CSV or Excel file (.csv, .xlsx, .xls).",
            "error"
        );
        return;
    }

    selectedFile = file;
    displaySelectedFile(file);
}


// =========================================================
// DISPLAY SELECTED FILE
// =========================================================

function displaySelectedFile(file) {
    const fileNameElement =
        document.getElementById("fileName");

    const fileSizeElement =
        document.getElementById("fileSize");

    const selectedFileElement =
        document.getElementById("selectedFile");

    const dropArea =
        document.getElementById("dropArea");

    const analyzeButton =
        document.getElementById("analyzeButton");

    if (fileNameElement) {
        fileNameElement.textContent = file.name;
    }

    if (fileSizeElement) {
        fileSizeElement.textContent =
            formatFileSize(file.size);
    }

    if (selectedFileElement) {
        selectedFileElement.style.display = "flex";
    }

    if (dropArea) {
        dropArea.style.display = "none";
    }

    if (analyzeButton) {
        analyzeButton.disabled = false;
    }
}


// =========================================================
// REMOVE SELECTED FILE
// =========================================================

function removeSelectedFile() {
    selectedFile = null;

    const fileInput =
        document.getElementById("fileInput");

    const selectedFileElement =
        document.getElementById("selectedFile");

    const dropArea =
        document.getElementById("dropArea");

    const analyzeButton =
        document.getElementById("analyzeButton");

    if (fileInput) {
        fileInput.value = "";
    }

    if (selectedFileElement) {
        selectedFileElement.style.display = "none";
    }

    if (dropArea) {
        dropArea.style.display = "flex";
    }

    if (analyzeButton) {
        analyzeButton.disabled = true;
    }
}


// =========================================================
// ANALYZE DATASET
// =========================================================

async function analyzeDataset() {
    if (!selectedFile) {
        showMessage(
            "Please select a dataset first.",
            "error"
        );
        return;
    }

    const analyzeButton =
        document.getElementById("analyzeButton");

    const originalText =
        analyzeButton
            ? analyzeButton.textContent
            : "";

    if (analyzeButton) {
        analyzeButton.disabled = true;
        analyzeButton.textContent =
            "Analyzing Dataset...";
    }

    try {
        const formData = new FormData();

        formData.append(
            "file",
            selectedFile
        );

        const response = await fetch(
            "http://127.0.0.1:5000/analyze",
            {
                method: "POST",
                body: formData
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.error ||
                "Dataset analysis failed."
            );
        }

        sessionStorage.setItem(
            "trainreadyReport",
            JSON.stringify(result)
        );

        sessionStorage.setItem(
            "trainreadyFileName",
            selectedFile.name
        );

        window.location.href =
            "results.html";

    } catch (error) {
        console.error(
            "Analysis Error:",
            error
        );

        showMessage(
            error.message ||
            "Cannot connect to the backend.",
            "error"
        );

        if (analyzeButton) {
            analyzeButton.disabled = false;
            analyzeButton.textContent =
                originalText ||
                "Analyze Dataset";
        }
    }
}


// =========================================================
// RESULTS PAGE INITIALIZATION
// =========================================================

function initializeResultsPage() {
    const isResultsPage =
        document.body.classList.contains("results-page");

    if (!isResultsPage) {
        return;
    }

    const storedReport =
        sessionStorage.getItem("trainreadyReport");

    if (!storedReport) {
        console.error(
            "No TrainReady report found."
        );
        return;
    }

    let report;

    try {
        report = JSON.parse(storedReport);
    } catch (error) {
        console.error(
            "Could not read saved report:",
            error
        );
        return;
    }

    loadDatasetName(report);
    loadTrainingReadiness(report);
    loadSummary(report);
    loadPreview(report);
    loadOverview(report);
    loadColumns(report);
    loadMissingValues(report);
    loadInsights(report);

    createDataTypeChart(report);
    createMissingChart(report);
    createTargetChart(report);
}


// =========================================================
// DATASET NAME
// =========================================================

function loadDatasetName(report) {
    const element =
        document.getElementById("datasetName");

    if (!element) {
        return;
    }

    const fileName =
        report?.dataset?.file_name ||
        sessionStorage.getItem("trainreadyFileName") ||
        "Dataset";

    element.textContent = fileName;
}


// =========================================================
// TRAINING READINESS
// =========================================================

function loadTrainingReadiness(report) {
    const card =
        document.getElementById("readinessCard");

    const icon =
        document.getElementById("readinessIcon");

    const title =
        document.getElementById("readinessTitle");

    const message =
        document.getElementById("readinessMessage");

    const issuesContainer =
        document.getElementById("readinessIssues");

    const percentageElement =
        document.getElementById("readinessPercentage");

    const progressBar =
        document.getElementById("readinessProgressBar");

    const reasonsContainer =
        document.getElementById("readinessReasons");

    if (!card || !title || !message) {
        return;
    }

    const readiness =
        report.training_readiness || {};

    card.classList.remove(
        "ready",
        "not-ready",
        "error"
    );

    if (issuesContainer) {
        issuesContainer.innerHTML = "";
    }

    if (reasonsContainer) {
        reasonsContainer.innerHTML = "";
    }

    let readinessPercentage =
        Number(readiness.readiness_percentage);

    if (!Number.isFinite(readinessPercentage)) {
        readinessPercentage = 0;
    }

    readinessPercentage =
        Math.max(
            0,
            Math.min(
                100,
                readinessPercentage
            )
        );

    if (percentageElement) {
        percentageElement.textContent =
            `${readinessPercentage.toFixed(0)}%`;
    }

    if (progressBar) {
        progressBar.style.width =
            `${readinessPercentage}%`;
    }

    const status =
        String(
            readiness.status || ""
        ).toUpperCase();

    let isReady = null;

    if (status === "READY") {
        isReady = true;
    } else if (
        status === "NOT READY" ||
        status === "NOT_READY"
    ) {
        isReady = false;
    } else if (
        status === "READY WITH WARNINGS" ||
        status === "READY_WITH_WARNINGS"
    ) {
        isReady = true;
    }

    displayReadinessReasons(
        readiness,
        reasonsContainer
    );

    if (
        status === "READY" ||
        isReady === true
    ) {
        card.classList.add("ready");

        if (icon) {
            icon.textContent = "✓";
        }

        if (
            status === "READY WITH WARNINGS" ||
            status === "READY_WITH_WARNINGS"
        ) {
            title.textContent =
                "READY WITH WARNINGS";

            message.textContent =
                readiness.readiness_summary ||
                "The dataset is mostly ready for training, but some issues should be reviewed before model training.";
        } else {
            title.textContent =
                "READY FOR TRAINING";

            message.textContent =
                readiness.readiness_summary ||
                "No major dataset-quality issues were detected by TrainReady. The dataset can proceed to the model-training stage.";
        }

        displayReadinessIssues(
            report,
            issuesContainer
        );

        return;
    }

    if (
        status === "NOT READY" ||
        status === "NOT_READY" ||
        isReady === false
    ) {
        card.classList.add("not-ready");

        if (icon) {
            icon.textContent = "⚠️";
        }

        title.textContent =
            "NOT READY FOR TRAINING";

        message.textContent =
            readiness.readiness_summary ||
            "Some issues were detected in your dataset. Review the reasons below before model training.";

        displayReadinessIssues(
            report,
            issuesContainer
        );

        return;
    }

    card.classList.add("error");

    if (icon) {
        icon.textContent = "⚠️";
    }

    title.textContent =
        "REVIEW DATASET";

    message.textContent =
        readiness.readiness_summary ||
        "TrainReady could not determine a final readiness status.";

    displayReadinessIssues(
        report,
        issuesContainer
    );
}


// =========================================================
// READINESS REASONS
// =========================================================

function displayReadinessReasons(readiness, container) {
    if (!container) {
        return;
    }

    let reasons = readiness.readiness_reasons;

    if (!Array.isArray(reasons)) {
        reasons = [];
    }

    if (reasons.length === 0) {
        container.innerHTML = `
            <div class="readiness-reason">
                <div class="readiness-reason-title">
                    Dataset Quality
                </div>

                <div class="readiness-reason-text">
                    No specific factors were reported as affecting training readiness.
                </div>
            </div>
        `;

        return;
    }

    reasons.forEach(reason => {
        if (!reason || typeof reason !== "object") {
            return;
        }

        const issue =
            reason.issue ||
            "Dataset issue";

        const description =
            reason.reason ||
            "This issue may affect training readiness.";

        const impact =
            Number(reason.impact || 0);

        const element =
            document.createElement("div");

        element.className =
            "readiness-reason";

        element.innerHTML = `
            <div class="readiness-reason-title">
                ${escapeHTML(issue)}
            </div>

            <div class="readiness-reason-text">
                ${escapeHTML(description)}
            </div>

            <div class="readiness-reason-impact">
                Readiness impact: −${impact}%
            </div>
        `;

        container.appendChild(element);
    });
}


// =========================================================
// READINESS ISSUES
// =========================================================

function displayReadinessIssues(
    report,
    container
) {
    if (!container) {
        return;
    }

    const issues = [];

    const qualityIssues =
        Array.isArray(report.quality_issues)
            ? report.quality_issues
            : [];

    qualityIssues.forEach(issue => {
        if (!issue) {
            return;
        }

        const type =
            issue.type ||
            issue.name ||
            issue.issue;

        if (!type) {
            return;
        }

        if (type === "Missing Values") {
            const details =
                issue.details || {};

            const columns =
                Object.keys(details);

            if (columns.length > 0) {
                issues.push(
                    `Missing values in ${columns.length} column(s)`
                );
            }

            return;
        }

        if (type === "Duplicate Rows") {
            const count =
                Number(issue.count || 0);

            if (count > 0) {
                issues.push(
                    `${formatNumber(count)} duplicate rows`
                );
            }

            return;
        }

        if (type === "Empty Rows") {
            const count =
                Number(issue.count || 0);

            if (count > 0) {
                issues.push(
                    `${formatNumber(count)} empty rows`
                );
            }

            return;
        }

        if (type === "Empty Columns") {
            if (
                Array.isArray(issue.columns) &&
                issue.columns.length > 0
            ) {
                issues.push(
                    `${issue.columns.length} empty column(s)`
                );
            }

            return;
        }

        if (type === "Constant Columns") {
            if (
                Array.isArray(issue.columns) &&
                issue.columns.length > 0
            ) {
                issues.push(
                    `${issue.columns.length} constant column(s)`
                );
            }

            return;
        }

        if (type === "Possible ID Columns") {
            if (
                Array.isArray(issue.columns) &&
                issue.columns.length > 0
            ) {
                issues.push(
                    `${issue.columns.length} possible ID column(s) to review`
                );
            }

            return;
        }

        if (type === "High Cardinality") {
            if (
                Array.isArray(issue.columns) &&
                issue.columns.length > 0
            ) {
                issues.push(
                    `${issue.columns.length} high-cardinality column(s) to review`
                );
            }

            return;
        }

        if (
            type ===
            "Inconsistent Categorical Values"
        ) {
            if (
                issue.details &&
                Object.keys(issue.details).length > 0
            ) {
                issues.push(
                    "Inconsistent categorical values"
                );
            }

            return;
        }

        issues.push(type);
    });

    if (hasAnalysisIssues(report.invalid_data)) {
        issues.push(
            "Invalid data detected"
        );
    }

    if (
        hasAnalysisIssues(
            report.incorrect_data_types
        )
    ) {
        issues.push(
            "Incorrect data types detected"
        );
    }

    if (
        hasAnalysisIssues(
            report.noise_detection
        )
    ) {
        issues.push(
            "Possible noisy data detected"
        );
    }

    if (
        hasAnalysisIssues(
            report.redundant_data
        )
    ) {
        issues.push(
            "Redundant data detected"
        );
    }

    if (
        hasAnalysisIssues(
            report.possible_data_leakage
        )
    ) {
        issues.push(
            "Possible data leakage detected"
        );
    }

    const uniqueIssues =
        [...new Set(issues)];

    if (uniqueIssues.length === 0) {
        container.innerHTML = `
            <div class="readiness-issue">
                No additional issues detected.
            </div>
        `;
        return;
    }

    uniqueIssues.forEach(issue => {
        const element =
            document.createElement("div");

        element.className =
            "readiness-issue";

        element.textContent =
            issue;

        container.appendChild(element);
    });
}


// =========================================================
// SUMMARY
// =========================================================

function loadSummary(report) {
    const summary =
        report.summary || {};

    setText(
        "totalRows",
        formatNumber(summary.rows || 0)
    );

    setText(
        "totalColumns",
        formatNumber(summary.columns || 0)
    );

    setText(
        "totalCells",
        formatNumber(summary.total_cells || 0)
    );

    setText(
        "duplicateRows",
        formatNumber(
            summary.duplicate_rows || 0
        )
    );
}


// =========================================================
// DATASET PREVIEW
// =========================================================

function loadPreview(report) {
    const container =
        document.getElementById(
            "previewContainer"
        );

    if (!container) {
        return;
    }

    const preview =
        report.preview || {};

    const firstRows =
        Array.isArray(
            preview.first_3_rows
        )
            ? preview.first_3_rows
            : [];

    const lastRows =
        Array.isArray(
            preview.last_3_rows
        )
            ? preview.last_3_rows
            : [];

    if (
        firstRows.length === 0 &&
        lastRows.length === 0
    ) {
        container.innerHTML =
            "<p>No preview available.</p>";
        return;
    }

    const rows = [];

    firstRows.forEach(row => {
        rows.push({
            row: row,
            type: "First rows"
        });
    });

    lastRows.forEach(row => {
        rows.push({
            row: row,
            type: "Last rows"
        });
    });

    const columns =
        report.column_names ||
        getColumnsFromRows(rows);

    let html = `
        <table class="result-table">
            <thead>
                <tr>
                    <th>Row</th>
    `;

    columns.forEach(column => {
        html += `
            <th>
                ${escapeHTML(column)}
            </th>
        `;
    });

    html += `
                </tr>
            </thead>

            <tbody>
    `;

    rows.forEach((item, index) => {
        html += `
            <tr>
                <td>
                    ${item.type} ${index + 1}
                </td>
        `;

        columns.forEach(column => {
            const value =
                item.row?.[column];

            html += `
                <td>
                    ${escapeHTML(
                        formatValue(value)
                    )}
                </td>
            `;
        });

        html += `
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}


// =========================================================
// DATASET OVERVIEW
// =========================================================

function loadOverview(report) {
    const container =
        document.getElementById(
            "overviewContainer"
        );

    if (!container) {
        return;
    }

    const summary =
        report.summary || {};

    const dataset =
        report.dataset || {};

    const items = [
        [
            "File Name",
            dataset.file_name || "—"
        ],
        [
            "File Type",
            dataset.file_type || "—"
        ],
        [
            "Rows",
            formatNumber(summary.rows || 0)
        ],
        [
            "Columns",
            formatNumber(summary.columns || 0)
        ],
        [
            "Total Cells",
            formatNumber(summary.total_cells || 0)
        ],
        [
            "Dataset Size",
            summary.dataset_size || "—"
        ],
        [
            "Duplicate Rows",
            formatNumber(
                summary.duplicate_rows || 0
            )
        ],
        [
            "Missing Values",
            formatNumber(
                summary.total_missing_values || 0
            )
        ]
    ];

    let html = "";

    items.forEach(item => {
        html += `
            <div class="overview-item">
                <span>
                    ${escapeHTML(item[0])}
                </span>

                <strong>
                    ${escapeHTML(
                        String(item[1])
                    )}
                </strong>
            </div>
        `;
    });

    container.innerHTML = html;
}


// =========================================================
// COLUMNS
// =========================================================

function loadColumns(report) {
    const container =
        document.getElementById(
            "columnsContainer"
        );

    if (!container) {
        return;
    }

    const columns =
        report.columns || {};

    const columnNames =
        report.column_names || [];

    if (columnNames.length === 0) {
        container.innerHTML =
            "<p>No columns found.</p>";
        return;
    }

    let html = "";

    columnNames.forEach(column => {
        const information =
            columns[column] || {};

        const dataType =
            information.data_type ||
            report.data_types?.[column] ||
            "Unknown";

        const unique =
            information.unique_values;

        html += `
            <div class="column-item">
                <div>
                    <div class="column-name">
                        ${escapeHTML(column)}
                    </div>

                    <div class="data-type">
                        ${escapeHTML(
                            String(dataType)
                        )}
                    </div>
                </div>

                ${
                    unique !== undefined
                        ? `
                            <div class="data-type">
                                ${formatNumber(unique)}
                                unique
                            </div>
                        `
                        : ""
                }
            </div>
        `;
    });

    container.innerHTML = html;
}


// =========================================================
// MISSING VALUES
// =========================================================

function loadMissingValues(report) {
    const container =
        document.getElementById(
            "missingContainer"
        );

    if (!container) {
        return;
    }

    const qualityIssues =
        Array.isArray(
            report.quality_issues
        )
            ? report.quality_issues
            : [];

    const missingIssue =
        qualityIssues.find(
            issue =>
                issue &&
                issue.type ===
                "Missing Values"
        );

    if (
        !missingIssue ||
        !missingIssue.details ||
        Object.keys(
            missingIssue.details
        ).length === 0
    ) {
        container.innerHTML = `
            <div class="no-missing">
                ✓ No missing values detected
            </div>
        `;
        return;
    }

    let html =
        '<div class="missing-list">';

    Object.entries(
        missingIssue.details
    ).forEach(
        ([column, information]) => {
            const count =
                information?.count || 0;

            const percentage =
                information?.percentage || 0;

            html += `
                <div class="missing-item">
                    <span class="missing-column">
                        ${escapeHTML(column)}
                    </span>

                    <span class="missing-count">
                        ${formatNumber(count)}
                        (${Number(
                            percentage
                        ).toFixed(2)}%)
                    </span>
                </div>
            `;
        }
    );

    html += "</div>";

    container.innerHTML = html;
}


// =========================================================
// KEY INSIGHTS
// =========================================================

function loadInsights(report) {
    const container =
        document.getElementById("insightsContainer");

    if (!container) {
        return;
    }

    const insights = [];

    const summary =
        report.summary || {};

    if (summary.rows) {
        insights.push(
            `Dataset contains ${formatNumber(summary.rows)} rows.`
        );
    }

    if (summary.columns) {
        insights.push(
            `Dataset contains ${formatNumber(summary.columns)} columns.`
        );
    }

    if (
        summary.total_missing_values &&
        summary.total_missing_values > 0
    ) {
        insights.push(
            `${formatNumber(summary.total_missing_values)} missing value(s) were detected.`
        );
    } else {
        insights.push(
            "No missing values were detected."
        );
    }

    if (
        summary.duplicate_rows &&
        summary.duplicate_rows > 0
    ) {
        insights.push(
            `${formatNumber(summary.duplicate_rows)} duplicate row(s) were detected.`
        );
    } else {
        insights.push(
            "No duplicate rows were detected."
        );
    }

    const target =
        report.target_analysis?.detection;

    if (
        target &&
        target.detected &&
        target.column
    ) {
        insights.push(
            `Possible target column detected: ${target.column}.`
        );
    }

    const readiness =
        report.training_readiness || {};

    const readinessStatus =
        String(
            readiness.status || ""
        ).toUpperCase();

    if (readinessStatus === "READY") {
        insights.push(
            "TrainReady assessment indicates that the dataset is ready for training."
        );
    } else if (
        readinessStatus === "READY WITH WARNINGS" ||
        readinessStatus === "READY_WITH_WARNINGS"
    ) {
        insights.push(
            "The dataset is mostly ready for training, but some issues should be reviewed."
        );
    } else if (
        readinessStatus === "NOT READY" ||
        readinessStatus === "NOT_READY"
    ) {
        insights.push(
            "The dataset should be reviewed and cleaned before training."
        );
    }

    let html = "";

    insights.forEach((insight, index) => {
        html += `
            <div class="insight-item">

                <div class="insight-number">
                    ${index + 1}
                </div>

                <div class="insight-text">
                    ${escapeHTML(insight)}
                </div>

            </div>
        `;
    });

    container.innerHTML = html;
}


// =========================================================
// DATA TYPE CHART
// =========================================================

function createDataTypeChart(report) {
    const canvas =
        document.getElementById(
            "dataTypeChart"
        );

    if (!canvas) {
        return;
    }

    const dataTypes =
        report.data_types || {};

    const counts = {};

    Object.values(dataTypes).forEach(type => {
        let cleanType =
            String(type);

        if (cleanType.includes("int")) {
            cleanType = "Integer";
        } else if (
            cleanType.includes("float")
        ) {
            cleanType = "Float";
        } else if (
            cleanType.includes("object") ||
            cleanType.includes("string")
        ) {
            cleanType = "Text";
        } else if (
            cleanType.includes("bool")
        ) {
            cleanType = "Boolean";
        } else if (
            cleanType.includes("datetime")
        ) {
            cleanType = "Date/Time";
        }

        counts[cleanType] =
            (counts[cleanType] || 0) + 1;
    });

    const labels =
        Object.keys(counts);

    const values =
        Object.values(counts);

    if (dataTypeChartInstance) {
        dataTypeChartInstance.destroy();
    }

    dataTypeChartInstance =
        new Chart(
            canvas,
            {
                type: "doughnut",

                plugins: [
                    percentageLabelsPlugin
                ],

                data: {
                    labels: labels,

                    datasets: [
                        {
                            data: values
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            position: "bottom"
                        },

                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const total =
                                        context.dataset.data.reduce(
                                            (sum, value) =>
                                                sum +
                                                Number(value),
                                            0
                                        );

                                    const value =
                                        Number(
                                            context.raw
                                        );

                                    const percentage =
                                        total > 0
                                            ? (
                                                value /
                                                total *
                                                100
                                            ).toFixed(1)
                                            : 0;

                                    return (
                                        `${context.label}: ` +
                                        `${value} ` +
                                        `(${percentage}%)`
                                    );
                                }
                            }
                        }
                    }
                }
            }
        );
}


// =========================================================
// MISSING VALUES CHART
// =========================================================

function createMissingChart(report) {
    const canvas =
        document.getElementById(
            "missingChart"
        );

    const chartCard =
        document.getElementById(
            "missingChartCard"
        );

    if (!canvas) {
        return;
    }

    const qualityIssues =
        Array.isArray(
            report.quality_issues
        )
            ? report.quality_issues
            : [];

    const missingIssue =
        qualityIssues.find(
            issue =>
                issue &&
                issue.type ===
                "Missing Values"
        );

    const details =
        missingIssue?.details || {};

    const labels =
        Object.keys(details);

    const values =
        labels.map(
            column =>
                Number(
                    details[column]?.count || 0
                )
        );

    if (missingChartInstance) {
        missingChartInstance.destroy();
    }

    if (labels.length === 0) {
        if (chartCard) {
            chartCard.style.display = "none";
        }
        return;
    }

    if (chartCard) {
        chartCard.style.display = "block";
    }

    missingChartInstance =
        new Chart(
            canvas,
            {
                type: "bar",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label:
                                "Missing Values",

                            data: values
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    scales: {
                        y: {
                            beginAtZero: true,

                            ticks: {
                                precision: 0
                            }
                        }
                    },

                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            }
        );
}


// =========================================================
// TARGET CHART
// =========================================================

function createTargetChart(report) {
    const canvas =
        document.getElementById(
            "targetChart"
        );

    const description =
        document.getElementById(
            "targetChartDescription"
        );

    if (!canvas) {
        return;
    }

    const detection =
        report.target_analysis?.detection;

    const distribution =
        report.target_analysis?.distribution;

    if (
        !detection ||
        !detection.detected ||
        !detection.column ||
        !distribution ||
        !distribution.available
    ) {
        if (description) {
            description.textContent =
                "No target distribution available";
        }

        if (targetChartInstance) {
            targetChartInstance.destroy();
            targetChartInstance = null;
        }

        return;
    }

    const classes =
        distribution.classes || [];

    const labels =
        classes.map(
            item =>
                typeof item === "object"
                    ? (
                        item.class ??
                        item.label ??
                        item.value
                    )
                    : item
        );

    const values =
        classes.map(
            item =>
                typeof item === "object"
                    ? Number(
                        item.count ??
                        item.value_count ??
                        0
                    )
                    : 0
        );

    if (labels.length === 0) {
        return;
    }

    if (description) {
        description.textContent =
            `Target: ${detection.column}`;
    }

    if (targetChartInstance) {
        targetChartInstance.destroy();
    }

    targetChartInstance =
        new Chart(
            canvas,
            {
                type: "doughnut",

                plugins: [
                    percentageLabelsPlugin
                ],

                data: {
                    labels: labels,

                    datasets: [
                        {
                            data: values
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            position: "bottom"
                        },

                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const total =
                                        context.dataset.data.reduce(
                                            (sum, value) =>
                                                sum +
                                                Number(value),
                                            0
                                        );

                                    const value =
                                        Number(
                                            context.raw
                                        );

                                    const percentage =
                                        total > 0
                                            ? (
                                                value /
                                                total *
                                                100
                                            ).toFixed(1)
                                            : 0;

                                    return (
                                        `${context.label}: ` +
                                        `${value} ` +
                                        `(${percentage}%)`
                                    );
                                }
                            }
                        }
                    }
                }
            }
        );
}


// =========================================================
// UTILITY - CHECK ANALYSIS ISSUES
// =========================================================

function hasAnalysisIssues(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return false;
    }

    if (Array.isArray(value)) {
        return value.length > 0;
    }

    if (typeof value === "object") {
        return Object.keys(value).length > 0;
    }

    if (typeof value === "string") {
        return value.trim().length > 0;
    }

    return Boolean(value);
}


// =========================================================
// UTILITY - FORMAT NUMBER
// =========================================================

function formatNumber(value) {
    const number =
        Number(value);

    if (Number.isNaN(number)) {
        return "0";
    }

    return number.toLocaleString("en-IN");
}


// =========================================================
// UTILITY - FORMAT FILE SIZE
// =========================================================

function formatFileSize(bytes) {
    if (!bytes) {
        return "0 Bytes";
    }

    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];

    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );

    return (
        parseFloat(
            (
                bytes /
                Math.pow(
                    1024,
                    index
                )
            ).toFixed(2)
        ) +
        " " +
        units[index]
    );
}


// =========================================================
// UTILITY - FORMAT VALUE
// =========================================================

function formatValue(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "—";
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return String(value);
}


// =========================================================
// UTILITY - GET COLUMNS FROM ROWS
// =========================================================

function getColumnsFromRows(rows) {
    const columns = [];

    rows.forEach(item => {
        if (!item.row) {
            return;
        }

        Object.keys(item.row).forEach(column => {
            if (!columns.includes(column)) {
                columns.push(column);
            }
        });
    });

    return columns;
}


// =========================================================
// UTILITY - ESCAPE HTML
// =========================================================

function escapeHTML(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// =========================================================
// UTILITY - SET TEXT
// =========================================================

function setText(id, value) {
    const element =
        document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


// =========================================================
// MESSAGE
// =========================================================

function showMessage(
    message,
    type = "info"
) {
    console.log(
        `[${type}] ${message}`
    );

    const toast =
        document.getElementById("toast");

    if (toast) {
        toast.textContent = message;

        toast.className =
            `toast ${type}`;

        toast.style.display =
            "block";

        setTimeout(
            function () {
                toast.style.display =
                    "none";
            },
            4000
        );

        return;
    }

    alert(message);
}