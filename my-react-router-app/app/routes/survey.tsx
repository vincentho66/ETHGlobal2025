// app/routes/survey.tsx
import type { Route } from "./+types/survey";

export function meta({}: Route.MetaArgs) {
    return [{ title: "Survey" }];
}

export default function Survey() {
    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Survey</h1>
            <form>
                {/* Add your survey questions here */}
                <div className="mb-4">
                    <label htmlFor="question1" className="block text-gray-700">
                        Question 1:
                    </label>
                    <input
                        type="text"
                        id="question1"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                    />
                </div>
                {/* Add more questions as needed */}
                <button
                    type="submit"
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                >
                    Submit
                </button>
            </form>
        </div>
    );
}
