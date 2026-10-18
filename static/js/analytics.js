/**
 * Analytics Dashboard Chart.js Visualizations.
 * Renders interactive charts using live MongoDB Aggregation pipeline datasets.
 */

document.addEventListener("DOMContentLoaded", function () {
    // -------------------------------------------------------------
    // Chart 1: Department Performance (Bar Chart) - Pipeline 3
    // -------------------------------------------------------------
    const deptCtx = document.getElementById("deptPerformanceChart");
    if (deptCtx && typeof deptStatsData !== "undefined" && deptStatsData.length > 0) {
        const labels = deptStatsData.map(d => d.department);
        const avgMarks = deptStatsData.map(d => d.avg_marks);
        const avgAtt = deptStatsData.map(d => d.avg_attendance);

        new Chart(deptCtx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Average Marks (%)",
                        data: avgMarks,
                        backgroundColor: "#2563eb",
                        borderRadius: 6
                    },
                    {
                        label: "Average Attendance (%)",
                        data: avgAtt,
                        backgroundColor: "#06b6d4",
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + "%" }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.dataset.label}: ${ctx.raw}%`
                        }
                    }
                }
            }
        });
    }

    // -------------------------------------------------------------
    // Chart 2: Performance Categories (Doughnut Chart) - Pipeline 7
    // -------------------------------------------------------------
    const catCtx = document.getElementById("categoriesChart");
    if (catCtx && typeof categoriesData !== "undefined" && categoriesData.length > 0) {
        const catLabels = categoriesData.map(c => c.category);
        const catCounts = categoriesData.map(c => c.student_count);

        new Chart(catCtx, {
            type: "doughnut",
            data: {
                labels: catLabels,
                datasets: [{
                    data: catCounts,
                    backgroundColor: [
                        "#10b981", // Excellent (Green)
                        "#3b82f6", // Good (Blue)
                        "#f59e0b", // Average (Amber)
                        "#ef4444"  // Needs Improvement (Red)
                    ],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` ${ctx.label}: ${ctx.raw} students`
                        }
                    }
                }
            }
        });
    }

    // -------------------------------------------------------------
    // Chart 3: Course-wise Statistics (Horizontal Bar Chart) - Pipeline 5
    // -------------------------------------------------------------
    const courseCtx = document.getElementById("courseStatsChart");
    if (courseCtx && typeof courseStatsData !== "undefined" && courseStatsData.length > 0) {
        const courseLabels = courseStatsData.map(c => c.course_id);
        const avgScores = courseStatsData.map(c => c.avg_marks);
        const minScores = courseStatsData.map(c => c.min_marks);
        const maxScores = courseStatsData.map(c => c.max_marks);

        new Chart(courseCtx, {
            type: "bar",
            data: {
                labels: courseLabels,
                datasets: [
                    {
                        label: "Average Score",
                        data: avgScores,
                        backgroundColor: "#8b5cf6",
                        borderRadius: 4
                    },
                    {
                        label: "Max Score",
                        data: maxScores,
                        backgroundColor: "#10b981",
                        borderRadius: 4
                    },
                    {
                        label: "Min Score",
                        data: minScores,
                        backgroundColor: "#f87171",
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // -------------------------------------------------------------
    // Chart 4: Technical Skills Distribution - Pipeline 6
    // -------------------------------------------------------------
    const skillsCtx = document.getElementById("skillsChart");
    if (skillsCtx && typeof skillsData !== "undefined" && skillsData.length > 0) {
        const skillNames = skillsData.map(s => s.skill);
        const skillCounts = skillsData.map(s => s.student_count);

        new Chart(skillsCtx, {
            type: "bar",
            data: {
                labels: skillNames,
                datasets: [{
                    label: "Students with Skill",
                    data: skillCounts,
                    backgroundColor: "#f59e0b",
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: "y", // Horizontal bar chart
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }
});
