window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

window.dashAgGridComponentFunctions.StatusRenderer = function (props) {
    var v = props.value;
    var online = (v === true) ||
        (typeof v === "string" &&
         ["online", "deployed", "active", "running", "true"].indexOf(v.toLowerCase()) !== -1);
    var color = online ? "#16a34a" : "#dc2626";      // green / red
    var label = online ? "Online" : "Offline";
    var icon  = online ? "bi bi-check-circle-fill" : "bi bi-x-circle-fill";
    return React.createElement(
        "span",
        {
            title: label,
            style: {
                display: "inline-flex", alignItems: "center", gap: "6px",
                color: color, fontWeight: 600
            }
        },
        React.createElement("i", {
            className: icon,
            style: { color: color, fontSize: "0.95rem" }
        }),
        React.createElement("span", { style: { fontSize: "0.8rem" } }, label)
    );
};

window.dashAgGridComponentFunctions.RegisterToRenderer = function () {
    return React.createElement(
        "img",
        {
            src: "/assets/icon-ibisba.svg",
            className: "icon-column",
            title: "Register to IBISBA",
            alt: "Register to IBISBA"
        }
    );
};

window.dashAgGridComponentFunctions.XAIRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-search icon-column",
            title: "Explainability",
            alt: "Explainability"
        }
    );
};

window.dashAgGridComponentFunctions.DetailsIconRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-info-circle icon-column",
            title: "Details",
            alt: "Details"
        }
    );
};

window.dashAgGridComponentFunctions.EditIconRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-pencil-square icon-column",
            title: "Edit",
            alt: "Edit"
        }
    );
};

window.dashAgGridComponentFunctions.DeleteIconRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-trash icon-column",
            title: "Delete",
            alt: "Delete"
        }
    );
};
