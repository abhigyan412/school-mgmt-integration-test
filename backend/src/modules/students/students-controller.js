const asyncHandler = require("express-async-handler");
const {
    getAllStudents,
    addNewStudent,
    getStudentDetail,
    setStudentStatus,
    updateStudent,
    deleteStudent,
} = require("./students-service");

const handleGetAllStudents = asyncHandler(async (req, res) => {
    const { name, className, section, roll } = req.query;
    const students = await getAllStudents({ name, className, section, roll });
    res.status(200).json({
        success: true,
        data: students,
    });
});

const handleAddStudent = asyncHandler(async (req, res) => {
    const payload = req.body;
    const result = await addNewStudent(payload);
    res.status(201).json({
        success: true,
        message: result.message,
    });
});

const handleUpdateStudent = asyncHandler(async (req, res) => {
    const { id } = req.params;
    const payload = { ...req.body, userId: Number(id) };
    const result = await updateStudent(payload);
    res.status(200).json({
        success: true,
        message: result.message,
    });
});

const handleGetStudentDetail = asyncHandler(async (req, res) => {
    const { id } = req.params;
    const student = await getStudentDetail(Number(id));
    res.status(200).json({
        success: true,
        data: student,
    });
});

const handleStudentStatus = asyncHandler(async (req, res) => {
    const { id } = req.params;
    const { status } = req.body;
    const reviewerId = req.user?.id;
    const result = await setStudentStatus({
        userId: Number(id),
        reviewerId,
        status,
    });
    res.status(200).json({
        success: true,
        message: result.message,
    });
});

const handleDeleteStudent = asyncHandler(async (req, res) => {
    const { id } = req.params;
    const result = await deleteStudent(Number(id));
    res.status(200).json({
        success: true,
        message: result.message,
    });
});

module.exports = {
    handleGetAllStudents,
    handleGetStudentDetail,
    handleAddStudent,
    handleStudentStatus,
    handleUpdateStudent,
    handleDeleteStudent,
};