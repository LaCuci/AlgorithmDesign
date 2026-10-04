import Foundation
import PDFKit
import AppKit
// macOS-only visual review aid: swift scripts/render.swift PDF OUTPUT_DIRECTORY
let arguments = CommandLine.arguments
if arguments.count != 3 { fatalError("Usage: swift scripts/render.swift PDF OUTPUT_DIRECTORY") }
let file = URL(fileURLWithPath: arguments[1])
let output = URL(fileURLWithPath: arguments[2])
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
guard let document = PDFDocument(url: file) else { fatalError("Cannot read \(file.path)") }
for index in 0..<document.pageCount {
    let page = document.page(at: index)!
    let stem = String(format: "%03d", index + 1)
    let image = page.thumbnail(of: NSSize(width: 1400, height: 1850), for: .mediaBox)
    let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
    try bitmap.representation(using: .png, properties: [:])!.write(to: output.appendingPathComponent(stem + ".png"))
    try (page.string ?? "").write(to: output.appendingPathComponent(stem + ".txt"), atomically: true, encoding: .utf8)
}
print("Rendered \(document.pageCount) pages")
